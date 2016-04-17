
sigma = require 'linkurious/dist/sigma.require'

App =
  init: ->
    console.log new sigma
    a = sigma.parsers.json('data/arctic.json', {
      container: 'graph-container'
    })

module.exports = App
