
entities = require('creatures')
terra = require('terra/main')

exports.automaton =
  init: ->

    dim =
      h: $(".overlay-terra").height()
      w: $(".overlay-terra").width()

    cell = 15


    @t = new terra.Terrarium dim.w // cell, dim.h // cell,
      periodic: no
      trails: 0
      # background: [255, 255, 255]
      cellSize: cell
      insertAfter: document.getElementById('overlay_terra')

    g = new entities.Protein
      color: [0,0,0]
      gene_ref: "CDKN1A"
      symbol: "KER"

    @t.grid = @t.makeGrid [
      [g]
    ]

    @t.animate 50, =>
      console.log g
      g.age = 100
      console.log g

      @t.animate 100, ->
        console.log g

    $(".overlay-terra").find("canvas")
    .height(dim.h).width(dim.w)

  register: ->
    model_final = _.mapObject @models, (val, key) =>
      if key isnt 'commons' then _.extend val, @models.commons

    for a, b of _.omit model_final, 'commons'
      terra.registerCreature b
