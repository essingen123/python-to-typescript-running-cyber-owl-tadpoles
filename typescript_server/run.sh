
#!/bin/bash
podman build -t typescript-server .
podman run -d -p 3000:3000 --name ts-server typescript-server
sleep 5
xdg-open http://localhost:3000
podman logs -f ts-server
