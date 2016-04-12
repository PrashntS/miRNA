_ = require('./util')

# abstract factory that adds a superclass of baseCreature

class baseCreature
  constructor: ->
    @age = -1
    @initialEnergy = 50
    @maxEnergy = 100
    @efficiency = 0.7
    @size = 50
    @actionRadius = 1
    @sustainability = 2
    @reproduceLv = 0.70
    @moveLv = 0

  boundEnergy: ->
    if @energy > @maxEnergy
      @energy = @maxEnergy

  isDead: ->
    @energy <= 0

  reproduce: (neighbors) ->
    spots = _.filter(neighbors, (spot) ->
      !spot.creature
    )
    if spots.length
      step = spots[_.random(spots.length - 1)]
      coords = step.coords
      creature = factory.make(@type)
      successFn = (->
        @energy -= @initialEnergy
        true
      ).bind(this)
      failureFn = @wait
      {
        x: coords.x
        y: coords.y
        creature: creature
        successFn: successFn
        failureFn: failureFn
      }
    else
      false

  move: (neighbors) ->
    creature = this
    # first, look for creatures to eat
    spots = _.filter(neighbors, ((spot) ->
      spot.creature.size < @size
    ).bind(this))
    # if there's not enough food, try to move
    if spots.length < @sustainability
      spots = _.filter(neighbors, (spot) ->
        !spot.creature
      )
    # if we've got a spot to move to...
    if spots.length
      # ...pick one
      step = spots[_.random(spots.length - 1)]
      coords = step.coords
      successFn = (->
        foodEnergy = step.creature.energy * @efficiency
        # add foodEnergy if eating, subtract 10 if moving
        @energy = @energy + (foodEnergy or -10)
        # clear the original location
        false
      ).bind(this)
      {
        x: coords.x
        y: coords.y
        creature: creature
        successFn: successFn
      }
    else
      false

  wait: ->
    @energy -= 5
    true

  process: (neighbors, x, y) ->
    step = {}
    maxEnergy = @maxEnergy
    if @energy > maxEnergy * @reproduceLv and @reproduce
      step = @reproduce(neighbors)
    else if @energy > maxEnergy * @moveLv and @move
      step = @move(neighbors)
    creature = step.creature
    if creature
      creature.successFn = step.successFn or creature.wait
      creature.failureFn = step.failureFn or creature.wait
      {
        x: step.x
        y: step.y
        creature: creature
        observed: true
      }
    else
      @energy != @maxEnergy

class baseCA
  constructor: ->
    @age = -1

  actionRadius: 1

  boundEnergy: ->

  isDead: -> false

  process: (neighbors, x, y) ->

  wait: ->

class factory
  constructor: ->
    @types = {}

  make: (type, options) ->
    Creature = @types[type]
    return type
    if Creature then new Creature(options) else false

  registerCreature: (options, init) ->
    # required attributes
    type = options.type
    # only register classes that fulfill the creature contract
    if typeof type == 'string' and typeof types[type] == 'undefined'
      # set the constructor, including init if it's defined
      if typeof init == 'function'

        types[type] = ->
          @energy = @initialEnergy
          init.call this
          return

      else

        types[type] = ->
          @energy = @initialEnergy
          return

      color = options.color or options.colour
      # set the color randomly if none is provided
      if typeof color != 'object' or color.length != 3
        options.color = [
          _.random(255)
          _.random(255)
          _.random(255)
        ]
      types[type].prototype = new baseCreature
      types[type]::constructor = types[type]
      _.each options, (value, key) ->
        types[type].prototype[key] = value
        return
      types[type]::successFn = types[type]::wait
      types[type]::failureFn = types[type]::wait
      types[type]::energy = options.initialEnergy
      true
    else
      false
  registerCA: (options, init) ->
    # required attributes
    type = options.type
    # only register classes that fulfill the creature contract
    if typeof type == 'string' and typeof types[type] == 'undefined'
      # set the constructor, including init if it's defined
      types[type] = if typeof init == 'function' then (->
        init.call this
        return
      ) else (->
      )
      color = options.color = options.color or options.colour
      # set the color randomly if none is provided
      if typeof color != 'object' or color.length != 3
        options.color = [
          _.random(255)
          _.random(255)
          _.random(255)
        ]
      options.colorFn = options.colorFn or options.colourFn
      types[type].prototype = new baseCA
      types[type]::constructor = types[type]
      _.each options, (value, key) ->
        types[type].prototype[key] = value
        return
      true
    else
      false

module.exports = new factory
