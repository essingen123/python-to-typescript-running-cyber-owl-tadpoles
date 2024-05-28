import os
import subprocess as sp

def run_cmd(cmd, verbose=False):
    if verbose:
        print(f"Running command: {cmd}")
    return sp.run(cmd, shell=True, check=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout.decode('utf-8')

try:
    # Install nvm if not present
    if not os.path.exists(os.path.expanduser("~/.nvm/nvm.sh")):
        print("Installing nvm...")
        run_cmd("curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash", verbose=True)
        run_cmd('export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm install node', verbose=True)

    # Load nvm
    print("Loading nvm...")
    run_cmd('export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use node', verbose=True)

    # Create project directory and initialize Node.js project
    print("Setting up project directory...")
    os.makedirs('typescript_server', exist_ok=True)
    os.chdir('typescript_server')
    print("Initializing Node.js project...")
    run_cmd("npm init -y", verbose=True)
    print("Installing dependencies...")
    run_cmd("npm install typescript ts-node @types/node @types/express express three @types/three axios @types/axios", verbose=True)
    print("Initializing TypeScript...")
    run_cmd("npx tsc --init", verbose=True)

    # Create server.ts
    print("Creating server.ts...")
    with open('server.ts', 'w') as f:
        f.write("""
import express from 'express'; import path from 'path'; import axios from 'axios';
const app = express(); const port = 3000;
app.use(express.static(path.join(__dirname, 'public')));
app.get('/api/air-quality', async (req, res) => {
    try { const response = await axios.get('https://api.openaq.org/v1/latest'); res.json(response.data); }
    catch (error) { res.status(500).send(error.toString()); }
});
app.listen(port, () => { console.log(`Server is running at http://localhost:${port}`); });
""")

    # Create index.html
    print("Creating index.html...")
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

    # Create Dockerfile
    print("Creating Dockerfile...")
    with open('Dockerfile', 'w') as f:
        f.write("""
FROM node:14
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["npx", "ts-node", "server.ts"]
""")

    # Create run.sh
    print("Creating run.sh...")
    with open('run.sh', 'w') as f:
        f.write("""
#!/bin/bash
podman build -t typescript-server .
podman run -d -p 3000:3000 --name ts-server typescript-server
sleep 5
xdg-open http://localhost:3000
podman logs -f ts-server
""")

    os.chmod('run.sh', 0o755)
    print("Running the server...")
    sp.run('./run.sh', shell=True)

except Exception as e:
    print(f"Error: {e}")
