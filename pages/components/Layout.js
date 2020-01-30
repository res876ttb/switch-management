import Header from './Header'
import Container from '@material-ui/core/Container';

import '../styles/main.scss';

const Layout = props => (
  <div>
    <Header title={props.title} />
    <Container>
      {props.children}
    </Container>
  </div>
);

export default Layout;