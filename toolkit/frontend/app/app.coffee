
App = init: ->
  console.log 'App initialized!'

  elementary = new (terra.Terrarium)(20, 20)

  terra.registerCA
    type: 'elementary'
    alive: false
    ruleset: [1, 0, 0, 1, 0, 0, 1, 0].reverse()
    colorFn: ->
      if @alive then @color + ',1' else '0,0,0,0'
    process: (neighbors, x, y) ->
      if @age == y
        index = neighbors.filter((neighbor) ->
          neighbor.coords.y == y - 1
        ).map((neighbor) ->
          if neighbor.creature.alive then 1 else 0
        )
        index = parseInt(index.join(''), 2)
        @alive = if isNaN(index) then !x else @ruleset[index]
      true
  elementary.grid = elementary.makeGrid('elementary')
  # elementary.animate()
  elementary.grid = elementary.step(10)
  elementary.draw()

  models:
    gene:
      type: 'gene'
      symbol: undefined
      age: 0
      health: 100
      actionRadius: 1
      color: [30, 0, 30]
      colorFn: ->
        #: Returns the creature's color at each step.
        #: The color is determined on the basis of genes.
        @color

      mirna_gene_complex: (neighbors) ->
        spots = _.filter neighbors, (spot) =>
          return false if spot.creature.type isnt 'mirna'

          target_id = _.findIndex spot.creature.targets, (target) =>
            target.symbol is @symbol

          return target_id isnt -1

        if spots.length
          #: Order all the spots on the basis of least affinity
          spots = _.sortBy spots, (spot) =>
            target_id = _.findIndex spot.creature.targets, (target) =>
              target.symbol is @symbol

            return spot.creature.targets[target_id].affinity

          binding_mir = spots.first()

          complex_mir = terra.make 'mirna_gene_complex',
            coords: binding_mir.coords
            gene_ref: @
            mirna_ref: binding_mir.creature

          return {
            x: binding_mir.coords.x
            y: binding_mir.coords.y
            creature: complex_mir
            successFn: -> false
            failureFn: -> true
          }

        return false

      rrna_gene_complex: (neighbors) ->
        spots = _.filter neighbors, (spot) ->
          spot.creature.type is 'rrna'

        if spots.length
          binding_rrna = spots[_.random(spots.length - 1)]

          complex_rrna = terra.make 'rrna_gene_complex',
            coords: binding_rrna.coords
            gene_ref: @

          return {
            x: binding_rrna.coords.x
            y: binding_rrna.coords.y
            creature: complex_rrna
            successFn: -> false
            failureFn: -> true
          }

        return false

      dissociate: ->
        if @age > 100 or @health < 10
          dissociated = terra.make 'free_nucleotide',
            coords: @coords

          return {
            x: @coords.x
            y: @coords.y
            creature: dissociated
            successFn: -> false
            failureFn: -> true
          }

        return false

      move: (neighbors) ->
        #: Find the spots which are free.
        spots = _.filter neighbors, (spot) ->
          not spot.creature

        if spots.length
          #: We found a new spot.
          step = spots[_.random(spots.length - 1)]
          #: Move with a probability

          if _.random() > 25
            return {
              x: step.coords.x
              y: step.coords.y
              creature: @
              successFn: ->
                #: Clear the original Location
                false
              failureFn: -> true
            }

        #: Didn't move.
        false

      process: (neighbors, x, y) ->
        #: Increment the Age of gene.
        #: If we find a rRNA in neighbour, form rrna_gene_complex.
        #: If we find a miRNA in neighbour, form mirna_gene_complex.
        #: If age is more than age lambda, dissociate.
        #: If none of the above, then, move into any random empty neighbour
        #: with a probability P, or stay there.

        actions = [
          @mirna_gene_complex
          @rrna_gene_complex
          @dissociate
          @move
        ]

        #: Perform all the actions
        performance = _.map actions, (act) => act(@neighbour)

        #: Eliminate all the performances that resulted in a false
        accepted = _.filter performance, (p) -> p isnt false

        if accepted.length
          #: If ANY valid action was performed
          #: Randomly pick one action.
          #: TODO: The actions must happen on the basis of rate const.
          step = accepted[_.random(accepted.length - 1)]

          return {
            x: step.x
            y: step.y,
            creature: step.creature,
            observed: yes
          }

        #: No action were taken
        return false

    mirna:
      type: 'mirna'
      symbol: undefined
      age: 0
      targets: []

    mirna_gene_complex:
      type: 'mirna_gene_complex'
      gene_ref: undefined
      mirna_ref: undefined
      age: 0
      dGbinding: 0

    rrna:
      type: 'rrna'

    rrna_gene_complex:
      type: 'rrna_gene_complex'
      gene_ref: undefined
      age: 0

    protein:
      type: 'protein'

    free_nucleotide:
      type: 'free_nucleotide'

    source:
      type: 'source'

    sink:
      type: 'sink'

module.exports = App
