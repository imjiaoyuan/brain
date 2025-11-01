#!/bin/bash

if [ -z "$1" ]; then
    exit 1
fi

DOTFILES="$1"

cp "$DOTFILES/condarc" ~/.condarc
cp "$DOTFILES/bashrc" ~/.bashrc
cp "$DOTFILES/gitconfig" ~/.gitconfig
cp "$DOTFILES/Rprofile" ~/.Rprofile

sudo cp "$DOTFILES/conf/pacman.conf" /etc/
sudo cp "$DOTFILES/conf/64-language-selector-prefer.conf" /etc/fonts/conf.d/