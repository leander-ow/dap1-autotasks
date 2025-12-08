let
  # We pin to a specific nixpkgs commit for reproducibility.
  # Last updated: 2025-11-05. Check for new commits at https://status.nixos.org.
  pkgs = import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/3de8f8d73e35724bf9abef41f1bdbedda1e14a31.tar.gz") {};
in pkgs.mkShell {
  packages = [
    (pkgs.python3.withPackages (python-pkgs: with python-pkgs; [
        selenium
        requests
        markdownify
        beautifulsoup4
        python-dotenv
    ]))
  ];
}