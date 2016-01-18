_ = require('./util')
factory = require('./creature')
display = require('./display')
dom = require('./dom')

###*
# Create a grid and fill it by using a function, 2-d array, or uniform type
# @param  {*} content  if  function, fill grid according to fn(x, y)
#                      if array, fill grid cells with the creatureType
#                      if string, fill grid with that creatureType
#                      otherwise, create empty grid
# @return {grid}       a grid adhering to the above rules
###

###*
# Terrarium constructor function
# @param {int} width             number of cells in the x-direction
# @param {int} height            number of cells in the y-direction
# @param {object} options
#   @param {string} id           id assigned to the generated canvas
#   @param {int} cellSize        pixel width of each cell (default 10)
#   @param {string} insertAfter  id of the element to insert the canvas after
#   @param {float} trails        a number from [0, 1] indicating whether trails
#                                be drawn. Background Required.
#   @param {array} background    an RGB triplet for the canvas' background
###

class Terrarium
  constructor: (width, height, options) ->
    cellSize = undefined
    neighborhood = undefined
    # cast width and height to integers
    width = Math.ceil(width)
    height = Math.ceil(height)
    # set default options
    options = options or {}
    cellSize = options.cellSize or 10
    neighborhood = options.neighborhood or options.neighbourhood
    if typeof neighborhood == 'string'
      neighborhood = neighborhood.toLowerCase()
    @width = width
    @height = height
    @cellSize = cellSize
    @trails = options.trails
    @background = options.background
    @canvas = dom.createCanvasElement(width, height, cellSize, options.id,
                                      options.insertAfter, @background)
    @grid = []
    @nextFrame = false
    @hasChanged = false
    @getNeighborCoords = _.getNeighborCoordsFn(width, height,
                                               neighborhood == 'vonneumann',
                                               options.periodic)

  makeGrid: (content) ->
    grid = []
    type = typeof content
    x = 0
    _w = @width
    while x < _w
      grid.push []
      y = 0
      _h = @height
      while y < _h
        # grid[x].push factory.make(if type == 'function' then content(x, y) else if type == 'object' and content.length then (content[y] or [])[x] else if type == 'string' then content else undefined)
        grid[x].push if content then (content[y] or [])[x] else undefined
        y++
      x++
    grid

  ###*
  # Create a grid and fill it randomly with a set creature distribution
  # @param  {array} distribution   an array of arrays of the form
                                  [string 'creatureName', float fillPercent]
  ###

  makeGridWithDistribution: (distribution) ->
    current = undefined
    rand = 0
    grid = []
    x = 0
    _w = @width
    while x < _w
      grid.push []
      y = 0
      _h = @height
      while y < _h
        grid[x].push factory.make(_.pickRandomWeighted(distribution))
        y++
      x++
    grid

  ###*
  # Returns the next step of the simulation
  # @param  {} steps   the number of steps to run through before returning
  # @return {grid}     a new grid after <steps> || 1 steps
  ###

  step: (steps) ->
    self = this
    gridWidth = @width
    gridHeight = @height
    oldGrid = @grid
    newGrid = undefined
    eigenGrid = undefined

    copyAndRemoveInner = (origCreature) ->
      if origCreature
        # copy = _.clone(origCreature)#_.assign(new (origCreature.constructor), origCreature)
        return origCreature
        copy = new origCreature.constructor(_.clone(origCreature))
        dead = copy and copy.isDead()
        if dead and !self.hasChanged
          self.hasChanged = true
        copy.age++
        if !dead then copy else false
      else
        false

    copyAndRemove = (origCols) ->
      _.map origCols, copyAndRemoveInner

    # TODO: Switch coords to just x and y to be consistent w/ pickWinnerInner

    zipCoordsWithNeighbors = (coords) ->
      {
        coords: coords
        creature: oldGrid[coords.x][coords.y]
      }

    processLoser = (loser) ->
      loserCreature = loser.creature
      if loserCreature
        loserCreature.failureFn()
        loserCreature.boundEnergy()
      else
        loser.wait()
        loser.boundEnergy()
      return

    processCreaturesInner = (creature, x, y) ->
      if creature
        neighbors = _.map self.getNeighborCoords(x, y, creature.actionRadius),
        zipCoordsWithNeighbors

        result = creature.process neighbors, x, y

        if result
          for r in result
            eigenColumn = eigenGrid[r.x]
            returnedCreature = r.creature
            returnedY = r.y

            if not eigenColumn[returnedY]
              eigenColumn[returnedY] = []

            eigenColumn[returnedY].push
              x: x
              y: y
              creature: r.creature

            if not self.hasChanged and r.observed
              self.hasChanged = yes
        else
          if result and not self.hasChanged
            self.hasChanged = true
          processLoser creature

    # processCreaturesInner = (creature, x, y) ->
    #   if creature
    #     neighbors = _.map(self.getNeighborCoords(x, y, creature.actionRadius),
    #                       zipCoordsWithNeighbors)
    #     result = creature.process(neighbors, x, y)

    #     if typeof result == 'object'
    #       eigenColumn = eigenGrid[result.x]
    #       returnedCreature = result.creature
    #       returnedY = result.y
    #       if !eigenColumn[returnedY]
    #         eigenColumn[returnedY] = []
    #       eigenColumn[returnedY].push
    #         x: x
    #         y: y
    #         creature: returnedCreature
    #       if !self.hasChanged and result.observed
    #         self.hasChanged = true
    #     else
    #       if result and !self.hasChanged
    #         self.hasChanged = true
    #       processLoser creature
    #   return

    processCreatures = (column, x) ->
      _.each column, (creature, y) ->
        processCreaturesInner creature, x, y
        return
      return

    pickWinnerInner = (superposition, x, y) ->
      if superposition
        winner = superposition.splice(_.random(superposition.length - 1), 1)[0]
        winnerCreature = winner.creature
        # clear the original creature's square if successFn returns false
        if !winnerCreature.successFn()
          newGrid[winner.x][winner.y] = false
        # TDso many calls to this. Can we just run it once at the start of a step?
        winnerCreature.boundEnergy()
        # put the winner in its rightful place
        newGrid[x][y] = winnerCreature
        # ...and call wait() on the losers. We can do this without
        # affecting temporal consistency because all callbacks have
        # already been created with prior conditions
        _.each superposition, processLoser
      return

    pickWinner = (column, x) ->
      _.each column, (superposition, y) ->
        pickWinnerInner superposition, x, y
        return
      return

    if typeof steps != 'number'
      steps = 1
    while steps--
      @hasChanged = false
      oldGrid = if newGrid then _.clone(newGrid) else @grid
      # copy the old grid & remove dead creatures
      newGrid = _.map(oldGrid, copyAndRemove)
      # create an empty grid to hold creatures competing for the same square
      eigenGrid = @makeGrid()
      # Add each creature's intended destination to the eigenGrid
      _.each newGrid, processCreatures
      # Choose a winner from each of the eigenGrid's superpositions
      _.each eigenGrid, pickWinner
      if !@hasChanged
        return false
    newGrid

  ###*
  # Updates the canvas to reflect the current grid
  ###

  draw: ->
    display @canvas, @grid, @cellSize, @trails, @background
    return

  ###*
  # Starts animating the simulation. Can be called with only a function.
  # @param  {int}   steps   the simulation will stop after <steps> steps if
  # @param  {Function} fn   called as a callback once the animation finishes
  ###

  animate: (steps, fn) ->

    tick = ->
      grid = self.step()
      if grid
        self.grid = grid
        self.draw()
        if ++i != steps
          return self.nextFrame = requestAnimationFrame(tick)
      # if grid hasn't changed || reached last step
      self.nextFrame = false
      if fn
        fn()
      return

    if typeof steps == 'function'
      fn = steps
      steps = null
    if !@nextFrame
      i = 0
      self = this
      self.nextFrame = requestAnimationFrame(tick)
    return

  ###*
  # Stops a currently running animation
  ###

  stop: ->
    cancelAnimationFrame @nextFrame
    @nextFrame = false
    return

  ###*
  # Stops any currently running animation and cleans up the DOM
  ###

  destroy: ->
    canvas = @canvas
    @stop()
    canvas.parentNode.removeChild canvas
    return

module.exports = Terrarium
