
entities = require('creatures')

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

    console.log g

    @t.grid = @t.makeGrid [
      []
      []
      []
      []
      []
      ['','','',g]
    ]

    @t.animate(1)

    $(".overlay-terra").find("canvas")
    .height(dim.h).width(dim.w)

  register: ->
    model_final = _.mapObject @models, (val, key) =>
      if key isnt 'commons' then _.extend val, @models.commons

    for a, b of _.omit model_final, 'commons'
      terra.registerCreature b
