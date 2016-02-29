# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

rivets      = require('rivets').rvt
GraphUtils  = require('utils/graph')
templates =
  geneselect: require('views/geneselect')

class Graph extends GraphUtils.Graph
  constructor: (opts)->
    console.log opts
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
    $.getJSON "/api/graph?genes=SOX4"
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
            inreq: gene == 'SOX4'

        for mirna in data.miRNA_store
          @addNode
            id: mirna
            type: 'miRNA'
            color: '#91B93E'
            inreq: false

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
    genes: ['MCM7']
    mirna: []

    serialize: ->
      $.param
        genes: @genes
        mirna: @mirna
      , yes

  select_init: ->
    $('#uni_search').selectize
      valueField: 'symbol'
      labelField: 'symbol'
      searchField: ['symbol', 'name', 'summary']
      create: false,
      render:
        item: (item, escape) ->
          console.log item, escape
          "<p>#{escape(item.symbol)}</p>"
        option: (item, escape) ->
          """
          <div>
            <p>#{escape(item.symbol)} - #{item.name}</p>
          </div>
          """
      score: (search) ->
        score = @getScoreFunction search
        (item) -> score(item) * 1

      load: (query, callback) ->
        if not query.length
          return callback()
        $.ajax
          url: "/api/search?q=#{encodeURIComponent(query)}",
          type: 'GET',
          error: -> callback()
          success: (res) -> callback(res.data)

exports.interaction =
  init: ->
    width = $(".overlay-terra").width()
    height = $(".overlay-terra").height()

    uiview = new UserView
      elem: '#graphcanvas'
      edat: '#data_gui'

    uiview.init()
