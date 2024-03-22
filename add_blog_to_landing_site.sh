rm -r blog
cd static/blog
hugo
cd ../..
cp -r static/blog/public ./blog