# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

rivets      = require('rivets').rvt
GraphUtils  = require('utils/graph')
_ = require('lodash')

class Graph
  constructor: (opts)->
    @G = new jsnx.DiGraph
    @nodes = []
    @edges = []
    @r = {}

  fetch: (dat, func) ->
    $.getJSON "/api/graph?#{dat}"
    .done (dat) =>
      {target_list, host_list, miRNA_store, genes_store} = dat

      @miRNAs = _.union @miRNAs, miRNA_store

      @G.addNodesFrom miRNA_store
      @G.addNodesFrom genes_store
      @G.addEdgesFrom target_list
      @G.addEdgesFrom host_list

      console.log @G.nodesIter()
      @r = jsnx.toDictOfLists(@G)

      @i_nodes()
      @i_edges()

      if func then func()

  i_nodes: () ->
    for k, v of @r
      id = _.findIndex(@nodes, ['name', k])
      if id is -1
        @nodes.push
          name: k
          type: if _.indexOf(@miRNAs, k) > -1 then 'miRNA' else 'Gene'
          weight: v.length
      else
        @nodes[id].weight = v.length

  i_edges: () ->
    for src, v of @r
      for target in v
        dat =
          source: _.find @nodes, (d) -> d.name is src
          target: _.find @nodes, (d) -> d.name is target
        id = _.findIndex @edges, dat
        if id is -1 then @edges.push dat

class GraphView
  constructor: (opts)->
    @graph = new GraphUtils.Graph opts

  fetch_and_update: (dat) ->
    $.getJSON "/api/graph?#{dat}"
      .done (data) =>
        for gene in data.genes_store
          @graph.addNode
            id: gene
            type: 'Gene'
            color: '#8C6CDA'
            inreq: gene is 'CDKN1A'

        for mirna in data.miRNA_store
          @graph.addNode
            id: mirna
            type: 'miRNA'
            color: '#88EB58'
            inreq: mirna is 'CDKN1A'

        for edge in data.target_list
          @graph.addLink edge[0], edge[1], '10', 'target'

        for edge in data.host_list
          @graph.addLink edge[0], edge[1], '10', 'host'

        @graph.update()

class UserView
  constructor: (opts) ->
    @select_init()
    @bound_select_input = {}
    @select_init()
    @rivets_init()
    @toolbar_init()

  rivets_init: ->
    @rivets_view = rivets.bind($('#nodes'), {nodes: @bound_select_input})
    @bound_select_input.genes = ['RIN2']

  toolbar_init: ->
    @toolbar = $('.cd-stretchy-nav')
    @toolbar.find('.cd-nav-trigger').on 'click', =>
      @toolbar.toggleClass 'nav-is-visible'

  select_val: ->
    $.param(@bound_select_input, true)

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
        markup = """
          <div class="dropdown-card">
            <h1>#{obj.symbol}</h1>
            <p>#{obj.description}</p>
            <ul>
              <li>
                <strong>Targeted By</strong>: #{obj.targeted_by.length} miRNAs
              </li>
              <li>
                <strong>Host of (miRNA)</strong>:
                  #{obj.host_of?.symbol || 'N.A.'}
              </li>
              <li>
                <strong>ESID</strong>: #{obj.names[0]}
              </li>
            </ul>
          </div>
        """
        markup

    $('.mirna_select').select2 factory_select
      uri: '/api/mirna'
      placeholder: "Please Enter a Few miRNA"
      templateResult: (obj) ->
        return obj.text if obj.loading
        markup = """
          <div class="dropdown-card">
            <h1>#{obj.symbol}</h1>
            <ul>
              <li>
                <strong>Targets</strong>: #{obj.targets.length} Genes
              </li>
              <li>
                <strong>Host Gene</strong>: #{obj.host?.symbol || 'N.A.'}
              </li>
              <li>
                <strong><a href="#{obj.mirbase_url}">miRBase Link</a></strong>
              </li>
            </ul>
          </div>
        """
        markup

exports.interaction =
  mmn: ->
    width = $(".overlay-terra").width()
    height = $(".overlay-terra").height()
    ui = new UserView

    graph = new GraphView
      w: width
      h: height
      elem: '#graphcanvas'
      dat: ui.select_val

    graph.fetch_and_update("genes=CDKN1A")

    $('select.rivets').on 'change', ->
      graph.fetch_and_update(ui.select_val())


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


    $('#data_gui').html(gui.domElement)

    $('select.rivets').on 'change', =>
      graph_factory()

    graph_factory()

  node_val: ->
    @nodes
