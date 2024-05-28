
import express from 'express'; import path from 'path'; import axios from 'axios';
const app = express(); const port = 3000;
app.use(express.static(path.join(__dirname, 'public')));
app.get('/api/air-quality', async (req, res) => {
    try { const response = await axios.get('https://api.openaq.org/v1/latest'); res.json(response.data); }
    catch (error: any) { res.status(500).send(error.toString()); }
});
app.listen(port, () => { console.log(`Server is running at http://localhost:${port}`); });
