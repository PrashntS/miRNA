
automaton = require('automaton').automaton
interaction = require('interaction').interaction

App =
  init: ->
    @interaction = interaction
    @automaton = automaton
    @interaction.init()
    # @automaton.init()

module.exports = App
