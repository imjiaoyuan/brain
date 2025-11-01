#!/bin/bash

if [ -z "$1" ]; then
    exit 1
fi

DOTFILES="$1"

mkdir -p "$DOTFILES/conf" "$DOTFILES/misc"

cp ~/.condarc "$DOTFILES/condarc"
cp ~/.bashrc "$DOTFILES/bashrc"
cp ~/.gitconfig "$DOTFILES/gitconfig"
cp ~/.Rprofile "$DOTFILES/Rprofile"

cp /etc/pacman.conf "$DOTFILES/conf/"
cp /etc/fonts/conf.d/64-language-selector-prefer.conf "$DOTFILES/conf/"

pacman -Qqen > "$DOTFILES/misc/packages-official.txt"
pacman -Qqem > "$DOTFILES/misc/packages-archlinuxcn.txt"