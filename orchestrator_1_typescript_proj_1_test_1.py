import os
import subprocess as sp

def r(cmd):
    result = sp.run(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    if result.returncode: raise sp.CalledProcessError(result.returncode, cmd)
    return result.stdout.decode('utf-8')

try:
    if not os.path.exists(os.path.expanduser("~/.nvm/nvm.sh")):
        r("curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash")
    r('bash -c "source $HOME/.nvm/nvm.sh && nvm install 16 && nvm use 16"')
    
    os.makedirs('typescript_server', exist_ok=True)
    os.chdir('typescript_server')
    r("npm init -y")
    r("npm install typescript ts-node @types/node @types/express express three @types/three axios @types/axios")
    r("npx tsc --init")

    with open('server.ts', 'w') as f:
        f.write("""
import express from 'express'; import path from 'path'; import axios from 'axios';
const app = express(); const port = 3000;
app.use(express.static(path.join(__dirname, 'public')));
app.get('/api/air-quality', async (req, res) => {
    try { const response = await axios.get('https://api.openaq.org/v1/latest'); res.json(response.data); }
    catch (error: any) { res.status(500).send(error.toString()); }
});
app.listen(port, () => { console.log(`Server is running at http://localhost:${port}`); });
""")

    os.makedirs('public', exist_ok=True)
    with open('public/index.html', 'w') as f:
        f.write("""
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>3D Graph</title><style>body{margin:0;}canvas{display:block;}</style></head><body>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
let scene = new THREE.Scene(); let camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
let renderer = new THREE.WebGLRenderer(); renderer.setSize(window.innerWidth, window.innerHeight); document.body.appendChild(renderer.domElement);
let geometry = new THREE.BoxGeometry(); let material = new THREE.MeshBasicMaterial({color: 0x00ff00}); let cube = new THREE.Mesh(geometry, material);
scene.add(cube); camera.position.z = 5;
function animate() { requestAnimationFrame(animate); cube.rotation.x += 0.01; cube.rotation.y += 0.01; renderer.render(scene, camera); }
animate();
async function fetchAirQualityData() { try { const response = await fetch('/api/air-quality'); const data = await response.json(); console.log(data); }
catch (error) { console.error('Error fetching air quality data:', error); } }
fetchAirQualityData();
</script></body></html>
""")

    with open('Dockerfile', 'w') as f:
        f.write("""
FROM node:16
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["npx", "ts-node", "server.ts"]
""")

    with open('run.sh', 'w') as f:
        f.write("""
#!/bin/bash
podman rm -f ts-server
podman build -t typescript-server .
podman run -d -p 3000:3000 --name ts-server typescript-server
sleep 5
xdg-open http://localhost:3000
podman logs -f ts-server
""")

    os.chmod('run.sh', 0o755)
    sp.run('./run.sh', shell=True)

    r('git init')
    r('git add .')
    r('git commit -m "Initial commit"')
    r('git remote add origin https://github.com/essingen123/python-to-ts-cyber-owl-tadpoles.git')
    r('git push -u origin master')

except Exception as e:
    print(f"Error: {e}")
