
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
    # G.addNodesFrom [1],#2,3,4,5,[9,{color: '#008A00'}]],
    #   color: '#0064C7'

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

    @n = rivets.bind($('#nodes'), {nodes: @nodes})

    graph_factory = (opts) =>
      $.getJSON "/api/graph?#{$.param(@nodes, true)}"
      .done (dat) ->
        {target_list, host_list, miRNA_store, genes_store} = dat

        G.addNodesFrom miRNA_store,
          color: '#4ECDC4'

        G.addNodesFrom genes_store,
          color: '#F5AB35'

        G.addEdgesFrom target_list
        G.addEdgesFrom host_list

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
      maximumSelectionLength: 5
      templateResult: opts.templateResult
      templateSelection: (obj) -> obj.symbol or obj.text

    $('.gene_select').select2 factory_select
      uri: '/api/gene'
      placeholder: "Please Enter a Few Genes"
      templateResult: (obj) ->
        return obj.text if obj.loading
        markup = """
          <div>
            <p>#{obj.symbol}</p>
            <p>#{obj.description}</p>
          </div>
        """
        markup

    $('.mirna_select').select2 factory_select
      uri: '/api/mirna'
      placeholder: "Please Enter a Few miRNA"
      templateResult: (obj) ->
        return obj.text if obj.loading
        markup = """
          <div>
            <p>#{obj.symbol}</p>
            <p>#{obj.description}</p>
          </div>
        """
        markup

    $('select.rivets').on 'change', =>
      graph_factory()

  node_val: ->
    @nodes
