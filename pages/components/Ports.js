import Axios from 'axios';

class Ports extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      loading: true,
    }
  }

  componentDidMount() {
    this.getData();
  }

  render() {
    return (
      <div>
        This is Ports.
      </div>
    )
  }

  getData() {
    // Get data from server
    /*
    1. Extract description
    2. Map configuration to room number
    3. Extract ACL, shutdown, speed, vlan, stormControl
    4. Convert ACL to list readable
    4. Apply to react state.
    */
    Axios.post('/api/getData', {
      'type': 'show all config'
    }).then(res => {
      // Extract description
      /** 
       * From
       * running_configs: {
       *   switch_ip: {
       *     port_name: 'config'
       *   }
       * }
       * to
       * running_configs: {
       *   switch_ip: {
       *     port_name: {
       *       description: 'description',
       *       config: ['config1', ...]
       *     }, ...,
       *     acl: acl
       *   }
       * }
       */
      let running_configs = JSON.parse(res.data.result);
      let result = {};
      for (let ip in running_configs) {
        let running_config = running_configs[ip];
        let result1 = {};
        for (let port_name in running_config.port) {
          let config = running_config.port[port_name].split('\n');
          for (let i in config) {
            let line = config[i];
            if (line.indexOf('description') !== -1) {
              result1[port_name] = {
                description: line.split('description ')[1],
                config: config
              };
              break;
            }
          }
        }

        // Remove blank line
        for (let port_name in result1) {
          let port = result1[port_name];
          port.config.pop();
        }

        result1.acl = running_config.acl;
        result[ip] = result1;
      }
      return result;
    }).then(running_configs => {
      // Extract ACL, shutdown, speed, vlan, stormControl
      /** 
       * From
       * running_configs: {
       *   switch_ip: {
       *     port_name: {
       *       description: 'description',
       *       config: ['config1', ...]
       *     }, ...,
       *     acl: {
       *       name1: 'rule', ...
       *     }
       *   }
       * }
       * to
       * running_configs: {
       *   switch_ip: {
       *     port_name: {
       *       description: 'description',
       *       acl: 'rule',
       *       vlan: '',
       *       shutdown: '',
       *       speed: '',
       *       stormControl: '',
       *       ...
       *       other: ['config1', ...]
       *     }
       *   }
       * }
       */
      for (let ip in running_configs) {
        let running_config = running_configs[ip];
        console.log(running_config.acl);
        break;
      }
    }).catch(err => {
      if (err.response) {
        if (err.response.status == 404) {
          console.error('Response got 404');
        }
      } else {
        console.error(err);
      }
    });
  }
}

export default Ports;