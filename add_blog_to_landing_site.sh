rm -r blog
cd static/blog
hugo
cd ../..
cp -r static/blog/public ./blog

sleep 1

git add .
git commit -m "degub deploy"
git push origin dev