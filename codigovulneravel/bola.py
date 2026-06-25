Broken Object Level Authorization (BOLA)

app.get('/api/store/:storeId', (req, res) => {
    if (!req.user || req.user.store != req.params.storeId) return res.status(401).json({message: 'Unauthorized'});
    res.json({ success: true });
});