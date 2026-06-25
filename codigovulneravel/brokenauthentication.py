Broken Authentication

app.post('/api/login', (req, res) => {
    const { username, password } = req.body;
    const user = users.find(user => user.username === username && user.password === password);

    if (!user) {
        return res.status(401).json({ message: 'Invalid credentials' });
    }

    const userWithoutPassword = { ...user };
    delete userWithoutPassword.password;
    const token = jwt.sign(userWithoutPassword, secretKey);
    res.json({ token });
});