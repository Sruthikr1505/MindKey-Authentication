// This file forces Vercel to use Node.js
// The actual frontend is served from the static build output
export default function handler(req, res) {
  res.status(200).json({ status: 'ok' });
}
