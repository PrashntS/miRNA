
rivets = require('rivets').rvt

exports.interaction =
  init: ->
    class Fanck
      constructor: ->
        @message = ''
        @speed = 0
        @col = '#FFFFFF'
        @explode = () ->
          console.log "Hey"

    func = new Fanck

    gui = new dat.GUI
      autoPlace: false
    f1 = gui.addFolder 'conc'
    f2 = gui.addFolder 'colors'
    f1.add func, 'message'
    f1.add func, 'speed', -5, 5
    f2.add func, 'explode'
    f2.addColor func, 'col'

    G = new (jsnx.DiGraph)
    G.addNodesFrom [1],#2,3,4,5,[9,{color: '#008A00'}]],
      color: '#0064C7'

    # G.addCycle [1,2,3,4,5]

    # G.addEdgesFrom [[1,9], [9,1]]

    jsnx.draw G,
      element: '#graphcanvas'
      withLabels: true
      nodeStyle: fill: (d) ->
        d.data.color
      labelStyle: fill: 'white'
      stickyDrag: true
    , true

    a = 2

    @nodes = {}

    rivets.bind($('#nodes'), {nodes: @nodes})

    setInterval ()->
      return if a > 10
      G.addNodesFrom [a],
        color: '#0064C7'

      if _.random(1000) < 200
        G.addEdgesFrom [[a-1, a], [a, _.random(a)]]
      else
        G.addEdgesFrom [[a-1, a]]

      a += 1

    , 0.1

    $('#data_gui').html(gui.domElement)

    factory_select = (opts) ->
      ajax:
        url: opts.uri,
        dataType: 'json',
        delay: 250,
        data: (param) ->
          return {
            q__icontains: param.term
            _skip: (param.page - 1) * 20 if param.page and param.page > 0
            _limit: 20
          }
        processResults: (data, params) ->
          params.page = params.page || 1

          return {
            results: _.map data.data, (dat) ->
              dat.id = dat.symbol
              dat.text = dat.symbol
              dat
            pagination:
              more: data.has_more
          }
        cache: true
      escapeMarkup: (markup) -> markup
      placeholder: opts.placeholder
      minimumInputLength: 2
      maximumSelectionLength: 2
      templateResult: (obj) ->
        return obj.text if obj.loading
        markup = """
          <div>
            <p>#{obj.symbol}</p>
            <p>#{obj.description}</p>
          </div>
        """
        markup
      templateSelection: (obj) -> obj.symbol or obj.text

    $('.gene_select').select2 factory_select
      uri: '/api/gene'
      placeholder: "Please Enter a Few Genes"

    $('.mirna_select').select2 factory_select
      uri: '/api/mirna'
      placeholder: "Please Enter a Few miRNA"

  node_val: ->
    @nodes
