const zmq = require("zeromq");

export default (req, res) => {
  let data = req.body;
  // console.log(req.method, req.body);

  switch(data.type) {
    case 'show all config':
      let socket = new zmq.Request;
      socket.connect('tcp://localhost:5454');
      socket.send(JSON.stringify({
        'type': 'show all config'
      }));
      socket.receive().then(result => {
        res.status(200).json({
          result: result.toString()
        });
      });
  }
};