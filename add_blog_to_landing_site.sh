rm -r blog
cd static
hugo
cd ..
cp -r static/public ./blog

sleep 1

git add .
git commit -m "new deploy"
git push origin dev
