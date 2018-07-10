#!/bin/bash

base_dir=$(git rev-parse --show-toplevel)
git_dir="${base_dir}/.git"

if [[ ! -d "$git_dir" ]]; then
    echo "$base_dir is not a git directory." >&2
    exit 1
fi

copy_hook() {
    local from="$base_dir/gitutils/$1"
    local to="$git_dir/hooks/$2"
    if [ -L $to ] && ls -l $to |grep "\-> $from" &> /dev/null ; then
        return;
    fi
    echo "Create symlink $from to $to" >&2
    rm $to &> /dev/null
    ln -s $from $to
    chmod +x $to
}

copy_c2thrift_hook() {
    local from="$base_dir/gitutils/c2thrift/$1"
    local to="$git_dir/modules/c2thrift/hooks/$2"
    if [ -L $to ] && ls -l $to |grep "\-> $from" &> /dev/null ; then
        return;
    fi
    echo "Create symlink $from to $to" >&2
    rm $to &> /dev/null
    ln -s $from $to
    chmod +x $to
}

copy_hook post-merge-checkout post-merge
copy_hook post-merge-checkout post-checkout
copy_hook post-merge-checkout post-rewrite
copy_hook pre-push pre-push
copy_hook pre-rebase pre-rebase
copy_hook pre-commit pre-commit
copy_hook post-commit post-commit
copy_hook prepare-commit-msg prepare-commit-msg

# copy_c2thrift_hook pre-commit pre-commit
# copy_c2thrift_hook pre-push pre-push

exit 0;
