{
  description = "Dumb F1 Guessgame";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.devshell.url = "github:numtide/devshell";

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    devshell,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
        overlays = [devshell.overlays.default];
      };

      timple = pkgs.python311Packages.buildPythonPackage rec {
        pname = "timple";
        version = "0.1.8";

        src = pkgs.python311Packages.fetchPypi {
          inherit pname version;
          hash = "sha256-u8EgMA8BA6OpPlSg0ASRxLcIcv5psRIEcBpIicagXw8=";
        };

        doCheck = false;
        pyproject = false;

        # Build time deps
        nativeBuildInputs = with pkgs.python311Packages; [
          setuptools
        ];

        # Run time deps
        dependencies = with pkgs.python311Packages; [
          matplotlib
          numpy
        ];
      };

      fastf1 = pkgs.python311Packages.buildPythonPackage rec {
        pname = "fastf1";
        version = "3.4.0";

        src = pkgs.python311Packages.fetchPypi {
          inherit pname version;
          hash = "sha256-rCjJaM0W2m9Yk3dhHkMOdIqPiKtVqoXuELBasmA9ybA=";
        };

        doCheck = false;
        pyproject = true;

        # Build time deps
        nativeBuildInputs = with pkgs.python311Packages; [
          hatchling
          hatch-vcs
        ];

        # Run time deps
        dependencies = with pkgs.python311Packages; [
          matplotlib
          numpy
          pandas
          python-dateutil
          requests
          requests-cache
          scipy
          rapidfuzz
          websockets

          timple
        ];
      };

      myPython = pkgs.python311.withPackages (p:
        with p; [
          # Basic
          rich

          # Web
          flask
          flask-sqlalchemy
          flask-caching
          sqlalchemy
          requests

          # Test
          pytest

          fastf1

          # TODO: For some reason, listing those under fastf1.dependencies doesn't work???
          matplotlib
          numpy
          pandas
          python-dateutil
          requests-cache
          scipy
          rapidfuzz
          websockets
          timple
        ]);
    in {
      devShell = pkgs.devshell.mkShell {
        name = "Formula10";

        packages = with pkgs; [
          myPython

          sqlitebrowser

          nodejs_21
          nodePackages.sass
          nodePackages.postcss-cli
          nodePackages.autoprefixer
        ];

        # Use $1 for positional args
        commands = [
          {
            name = "vscode";
            help = "Launch VSCode";
            command = "code . &>/dev/null &";
          }
          {
            name = "pycharm";
            help = "Launch PyCharm Professional";
            command = "pycharm-professional . &>/dev/null &";
          }
          {
            name = "db";
            help = "Launch SQLiteBrowser";
            command = "sqlitebrowser ./instance/formula10.db &>/dev/null &";
          }
          {
            name = "api";
            help = "Launch Hoppscotch in Google Chrome";
            command = "google-chrome-stable https://hoppscotch.io &>/dev/null &";
          }
        ];
      };
    });
}
