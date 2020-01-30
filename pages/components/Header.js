import Link from 'next/link';
import Head from 'next/head';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Container from '@material-ui/core/Container';

const loginStyle = {
  marginRight: '0px'
}

const flexGrow = {
  flexGrow: 1
}

class Header extends React.Component {
  render() {
    let title = this.props.title;
    if (!title) title = 'NTHUCSCC IP';
    return (
      <div>
        <Head>
          <title>{title}</title>
        </Head>
        <AppBar position="static">
          <Container>
            <Toolbar style={{padding: '0px'}}>
              <Typography variant="h6" style={flexGrow}>
                {title}
              </Typography>
              <Button color="inherit" style={loginStyle}>Login</Button>
            </Toolbar>
          </Container>
        </AppBar>
      </div>
    )
  }
}

export default Header;