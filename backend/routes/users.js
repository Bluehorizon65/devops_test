const express = require('express');
const router = express.Router();

// In-memory users array for demo
const users = [
  { id: 1, name: 'Alice' },
  { id: 2, name: 'Bob' }
];

// GET /users
router.get('/', (req, res) => {
  res.json(users);
});

// GET /users/:id
router.get('/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  const user = users.find(u => u.id === id);
  if (!user) return res.status(404).json({ error: 'User not found' });
  res.json(user);
});

// POST /users
router.post('/', (req, res) => {
  const { name } = req.body || {};
  if (!name) return res.status(400).json({ error: 'Name is required' });
  const id = users.length ? users[users.length - 1].id + 1 : 1;
  const newUser = { id, name };
  users.push(newUser);
  res.status(201).json(newUser);
});

module.exports = router;
