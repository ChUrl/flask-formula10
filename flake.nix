{
  description = "Dumb F1 Guessgame";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.devshell.url = "github:numtide/devshell";

  outputs = { self, nixpkgs, flake-utils, devshell }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
          overlays = [ devshell.overlays.default ];
        };

        myPython = pkgs.python311.withPackages (p: with p; [
          # Basic
          rich
          numpy

          # Web
          flask
          flask-sqlalchemy
          sqlalchemy
          requests

          pytest
        ]);
      in {
        devShell = pkgs.devshell.mkShell {
          name = "Formula10";

          packages = with pkgs; [
            myPython

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
