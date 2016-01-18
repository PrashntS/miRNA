
automaton = require('automaton').automaton
interaction = require('interaction').interaction
_ = require('lodash/lodash')._

App =
  init: ->
    @interaction = interaction
    @automaton = automaton
    @interaction.init()
    # @automaton.init()

module.exports = App
