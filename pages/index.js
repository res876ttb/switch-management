import Layout from './components/Layout';
import Ports from './components/Ports';

class Index extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Layout title={'NTHUCSCC IP'}>
        <Ports />
      </Layout>
    )
  }
}

export default Index;