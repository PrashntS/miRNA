
# automaton = require './automaton'
interaction = require './interaction'

App =
  init: ->
    @interaction = interaction
    # @automaton = automaton
    @interaction.init()
    # @automaton.init()


module.exports = App
