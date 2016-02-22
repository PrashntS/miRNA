# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

rivets      = require('rivets').rvt
GraphUtils  = require('utils/graph')
templates =
  geneselect: require('views/geneselect')

class Graph extends GraphUtils.Graph
  constructor: (opts)->
    super opts
    @bindings = opts.ui_binding
    @_G = new jsnx.DiGraph

  node_click_handle: (node, f) =>
    if @bindings.toolbar_btm.eraser
      @removeNode(node.id)
      @_G.removeNode(node.id)

    if @bindings.toolbar_btm.info
      vex.dialog.alert
        message: node.id
        className: 'vex-theme-default'

  fetch_and_update: ->
    $.getJSON "/api/graph?#{@bindings.select2box.serialize()}"
      .done (data) =>
        @_G.addNodesFrom(data.genes_store)
        @_G.addNodesFrom(data.miRNA_store)
        @_G.addEdgesFrom(data.target_list)
        @_G.addEdgesFrom(data.host_list)

        for gene in data.genes_store
          @addNode
            id: gene
            type: 'Gene'
            color: '#8C6CDA'
            inreq: _.indexOf(@bindings.select2box.genes, gene) >= 0

        for mirna in data.miRNA_store
          @addNode
            id: mirna
            type: 'miRNA'
            color: '#91B93E'
            inreq: _.indexOf(@bindings.select2box.mirna, mirna) >= 0

        for edge in data.target_list
          @addLink edge[0], edge[1], '10', 'target'

        for edge in data.host_list
          @addLink edge[0], edge[1], '10', 'host'

        @update()

class UserParam
  constructor: (opts) ->
    @message = ''
    @speed = 0
    @col = '#FFFFFF'

class UserView
  constructor: (opts) ->
    @select2box = @select2box
    @toolbar_btm = @toolbar_btm
    @elem = opts.elem
    @edat = opts.edat

  init: ->
    @select_init()
    @rivets_init()
    @graph_init()
    # @param_init()
    @graph.fetch_and_update()
    @select2_event_init()

  param_init: ->
    @user_param = new UserParam

    @data_gui = {}

    @data_gui.dat = new dat.GUI
      autoPlace: false

    @data_gui.f_conc = @data_gui.dat.addFolder 'Concentration'
    @data_gui.f_color = @data_gui.dat.addFolder 'Colors'

    @data_gui.f_conc.add @user_param, 'message'
    @data_gui.f_conc.add @user_param, 'speed', -10, 10
    @data_gui.f_color.addColor @user_param, 'col', -10, 10

    $(@edat).html(@data_gui.dat.domElement)

  graph_init: ->
    @graph = new Graph
      w: $(@elem).width()
      h: $(@elem).height()
      elem: @elem
      ui_binding: @

  rivets_init: ->
    @rv_select_view = rivets.bind($('#nodes'), {nodes: @select2box})
    @rv_toolbar_view = rivets.bind $('#toolbar'), {toolbar: @toolbar_btm}

  toolbar_btm:
    show: yes
    eraser: no
    observe: no
    simulate: no
    info: no

    toggle: (e, f) ->
      key = e.currentTarget.dataset['target']
      new_state = not f.toolbar[key]

      #: Reset all other
      f.toolbar.eraser = false
      f.toolbar.observe = false
      f.toolbar.simulate = false
      f.toolbar.info = false

      f.toolbar[key] = new_state

    emit: (e, f) ->

  select2box:
    genes: ['RIN2']
    mirna: []

    serialize: ->
      $.param
        genes: @genes
        mirna: @mirna
      , yes

  select2_event_init: ->
    $('select.rivets').on 'select2:select', =>
      @graph.fetch_and_update()

    $('select.rivets').on 'select2:unselecting', =>
      @cache =
        genes: @select2box.genes
        mirna: @select2box.mirna

    $('select.rivets').on 'select2:unselect', (a, b)=>
      genes_rem = _.xor @cache.genes, @select2box.genes
      mirna_rem = _.xor @cache.mirna, @select2box.mirna

      for n in genes_rem
        @graph.removeNode(n)

      for n in mirna_rem
        @graph.removeNode(n)

  select_init: ->
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
      value: 'CDKN1A'
      placeholder: "Please Enter a Few Genes"
      templateResult: (obj) ->
        return obj.text if obj.loading
        templates.geneselect obj: obj

    # $('.mirna_select').select2 factory_select
    #   uri: '/api/mirna'
    #   placeholder: "Please Enter a Few miRNA"
    #   templateResult: (obj) ->
    #     return obj.text if obj.loading
    #     markup = """
    #       <div class="dropdown-card">
    #         <h1>#{obj.symbol}</h1>
    #         <ul>
    #           <li>
    #             <strong>Targets</strong>: #{obj.targets.length} Genes
    #           </li>
    #           <li>
    #             <strong>Host Gene</strong>: #{obj.host?.symbol || 'N.A.'}
    #           </li>
    #           <li>
    #             <strong><a href="#{obj.mirbase_url}">miRBase Link</a></strong>
    #           </li>
    #         </ul>
    #       </div>
    #     """
    #     markup

exports.interaction =
  init: ->
    width = $(".overlay-terra").width()
    height = $(".overlay-terra").height()

    uiview = new UserView
      elem: '#graphcanvas'
      edat: '#data_gui'

    uiview.init()
