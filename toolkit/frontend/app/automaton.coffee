
entities = require('creatures')
terra = require('terra/main')

exports.automaton =
  init: ->

    dim =
      h: $(".overlay-terra").height()
      w: $(".overlay-terra").width()

    cell = 50


    @t = new terra.Terrarium dim.w // cell, dim.h // cell,
      periodic: no
      trails: 0
      # background: [255, 255, 255]
      cellSize: cell
      insertAfter: document.getElementById('overlay_terra')

    g = new entities.Protein
      color: [0,100,0]
      gene_ref: "CDKN1A"
      symbol: "KER"

    g2 = () -> new entities.Gene
      color: [200, 10, 100]
      symbol: "CDKN1A"
      host_of: ["A", "B"],
      targeted_by: [
        {symbol: "C", affinity: 10}
        {symbol: "D", affinity: 20}
        {symbol: "E", affinity: 30}
      ]

    g3 = () -> new entities.miRNA
      color: [0, 100, 10]
      symbol: "C"

    g4 = new entities.miRNA
      color: [100, 100, 10]
      symbol: "E"

    g5 = new entities.miRNA
      color: [200, 10, 100]
      symbol: "H"


    h = new entities.Protein
      color: [100,0,0]
      gene_ref: "CDKN1A"
      symbol: "KER"

    @t.grid = @t.makeGrid [
      [g3(), g3(), g3(), g3(), g3()]
      []
      []
      [g3(), g2(), g3(), g3(), g3(), g3(), g3()]
    ]

    @t.animate 30, => console.log @t.grid

    $(".overlay-terra").find("canvas")
    .height(dim.h).width(dim.w)

  register: ->
    model_final = _.mapObject @models, (val, key) =>
      if key isnt 'commons' then _.extend val, @models.commons

    for a, b of _.omit model_final, 'commons'
      terra.registerCreature b
