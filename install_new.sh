DIR_TOOLCHAIN=../gap8_env/lib/gap_riscv_toolchain
if [ ! -d "$DIR_TOOLCHAIN" ]; then
    mkdir $DIR_TOOLCHAIN
    cp -rf ./* $DIR_TOOLCHAIN
    cd $DIR_TOOLCHAIN
    cd bin
    for eachFile in *
    do
        ln -fs $PWD/$eachFile ../gap8_env/bin/$eachFile
    done
else
    echo "$DIR_TOOLCHAIN already exist!!! Please remove it if you want to update"
fi
