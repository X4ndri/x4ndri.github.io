rm -r blog
cd static
hugo
cd ..
cp -r static/public ./blog

sleep 1

git add .
git commit -m "degub deploy"
git push origin main