module.exports = config:
  files:
    javascripts:
      joinTo:
        'js/libraries.js': /^(?!app\/)/
        'js/app.js': /^app\//
    stylesheets:
      joinTo:
        'css/libraries.css': /^(?!app\/)/
        'css/app.css': /^app\//
    templates: joinTo: 'js/app.js'
  plugins:
    coffeescript:
      bare: yes
    sass:
      mode: 'ruby'
      allowCache: true
      options:
        includePaths: (->
          bourbon = require('node-bourbon').includePaths
          neat = require('node-neat').includePaths
          bourbon.concat neat
        )()
    autoReload:
      enabled: yes
    lodash_template:
      variable: null
      namespace: "module.exports"
  npm:
    enabled: yes
    styles:
      'normalize.css': [
        'normalize.css'
      ]
