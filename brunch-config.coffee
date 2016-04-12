#!/usr/bin/env coffee
# Miriam
#

module.exports = config:
  paths:
    watched: ['app']

  npm:
    enabled: yes
    styles:
      'normalize-css': [
        'normalize.css'
      ]

  files:
    javascripts:
      joinTo:
        'js/libraries.js': /^(?!app\/)/
        'js/app.js': /^app\//
    stylesheets:
      joinTo:
        'css/libraries.css': /^(?!app\/)/
        'css/app.css': /^app\//

  plugins:
    coffeescript:
      bare: yes
    sass:
      mode: 'ruby'
      options:
        includePaths: [
          'node_modules/bourbon/app/assets/stylesheets'
          'node_modules/bourbon-neat/app/assets/stylesheets'
        ]

    autoReload:
      enabled: yes
