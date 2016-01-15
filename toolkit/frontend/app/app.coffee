
automaton = require('automaton').automaton
interaction = require('interaction').interaction

App =
  init: ->
    @interaction = interaction
    @interaction.init()

module.exports = App
