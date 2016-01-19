
automaton = require('automaton').automaton
interaction = require('interaction').interaction

App =
  init: ->
    @interaction = interaction
    @automaton = automaton
    @interaction.mmn()
    # @automaton.init()

module.exports = App
