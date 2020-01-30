const fs = require('fs');
const zmq = require("zeromq");

export default (req, res) => {
  // let socket = new zmq.Request;
  // socket.connect('tcp://localhost:3001');
  // console.log('Start to send string to python zmq server...');
  // socket.send('123');
  // socket.receive().then(result => {
  //   console.log(result.toString());
  // });

  let data = req.body;
  console.log(req.method, req.body);
  res.status(200).json({
    content: fs.readFileSync(data.filename).toString()
  });
};