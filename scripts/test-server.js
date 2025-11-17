const http = require('http');

console.log('Testing server...\n');

// Wait a bit for server to start
setTimeout(() => {
  const options = {
    hostname: 'localhost',
    port: 3000,
    path: '/health',
    method: 'GET'
  };

  const req = http.request(options, (res) => {
    let data = '';

    res.on('data', (chunk) => {
      data += chunk;
    });

    res.on('end', () => {
      console.log('✅ Server is running!');
      console.log('Response:', data);
      console.log('\nYou can now test the API endpoints.');
      console.log('See START_SERVER.md for examples.\n');
    });
  });

  req.on('error', (error) => {
    console.error('❌ Server is not responding:', error.message);
    console.log('\nMake sure the server is running with: npm run dev\n');
  });

  req.end();
}, 2000);
