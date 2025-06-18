'use client';

import { useState } from 'react';
import { 
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Box,
  Menu,
  MenuItem,
  Button,
  Avatar,
  Badge,
  Divider,
  useTheme
} from '@mui/material';
import { 
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  Mail as MailIcon,
  Settings as SettingsIcon,
  Search as SearchIcon,
  MoreVert as MoreIcon
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

interface HeaderProps {
  onToggleSidebar?: () => void;
}

/**
 * Application header component with navigation, search, and user actions
 * 
 * @param props - Component properties
 * @returns The application header component
 */
const Header: React.FC<HeaderProps> = ({ onToggleSidebar }) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [mobileMoreAnchorEl, setMobileMoreAnchorEl] = useState<null | HTMLElement>(null);
  const theme = useTheme();
  const { t } = useTranslation();

  const isMenuOpen = Boolean(anchorEl);
  const isMobileMenuOpen = Boolean(mobileMoreAnchorEl);

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>): void => {
    setAnchorEl(event.currentTarget);
  };

  const handleMobileMenuClose = (): void => {
    setMobileMoreAnchorEl(null);
  };

  const handleMenuClose = (): void => {
    setAnchorEl(null);
    handleMobileMenuClose();
  };

  const handleMobileMenuOpen = (event: React.MouseEvent<HTMLElement>): void => {
    setMobileMoreAnchorEl(event.currentTarget);
  };

  const menuId = 'primary-search-account-menu';
  const renderMenu = (
    <Menu
      anchorEl={anchorEl}
      id={menuId}
      keepMounted
      open={isMenuOpen}
      onClose={handleMenuClose}
      PaperProps={{
        elevation: 0,
        sx: {
          overflow: 'visible',
          filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.1))',
          mt: 1.5,
          borderRadius: 2,
          minWidth: 180,
          '& .MuiAvatar-root': {
            width: 32,
            height: 32,
            ml: -0.5,
            mr: 1,
          },
        },
      }}
      transformOrigin={{ horizontal: 'right', vertical: 'top' }}
      anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
    >
      <MenuItem onClick={handleMenuClose}>
        <Avatar sx={{ width: 24, height: 24, mr: 2 }} /> {t('Profile')}
      </MenuItem>
      <MenuItem onClick={handleMenuClose}>
        <SettingsIcon fontSize="small" sx={{ mr: 2 }} /> {t('Settings')}
      </MenuItem>
      <Divider />
      <MenuItem onClick={handleMenuClose}>
        {t('Logout')}
      </MenuItem>
    </Menu>
  );

  const mobileMenuId = 'primary-search-account-menu-mobile';
  const renderMobileMenu = (
    <Menu
      anchorEl={mobileMoreAnchorEl}
      anchorOrigin={{
        vertical: 'top',
        horizontal: 'right',
      }}
      id={mobileMenuId}
      keepMounted
      transformOrigin={{
        vertical: 'top',
        horizontal: 'right',
      }}
      open={isMobileMenuOpen}
      onClose={handleMobileMenuClose}
      PaperProps={{
        elevation: 0,
        sx: {
          overflow: 'visible',
          filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.1))',
          mt: 1.5,
          borderRadius: 2,
          minWidth: 180,
        },
      }}
    >
      <MenuItem>
        <IconButton size="large" color="inherit">
          <Badge badgeContent={4} color="error">
            <MailIcon />
          </Badge>
        </IconButton>
        <p>{t('Messages')}</p>
      </MenuItem>
      <MenuItem>
        <IconButton size="large" color="inherit">
          <Badge badgeContent={17} color="error">
            <NotificationsIcon />
          </Badge>
        </IconButton>
        <p>{t('Notifications')}</p>
      </MenuItem>
      <MenuItem onClick={handleProfileMenuOpen}>
        <IconButton
          size="large"
          aria-label="account of current user"
          aria-controls="primary-search-account-menu"
          aria-haspopup="true"
          color="inherit"
        >
          <Avatar sx={{ width: 24, height: 24 }} />
        </IconButton>
        <p>{t('Profile')}</p>
      </MenuItem>
    </Menu>
  );

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar 
        position="static" 
        color="default" 
        elevation={0}
        sx={{ 
          backgroundColor: 'background.paper',
          borderBottom: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Toolbar>
          <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
            <IconButton
              edge="start"
              color="inherit"
              aria-label="open drawer"
              onClick={onToggleSidebar}
              sx={{ display: { xs: 'flex', md: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
            <Box 
              component="img"
              src="/assets/turtle-brand.png"
              alt="Logo"
              sx={{ 
                height: 60,
                ml: { xs: 1, sm: 2 },
                display: { xs: 'none', sm: 'block' }
              }}
            />
          </Box>
          
          <Box sx={{ flexGrow: 1 }} />
          
          <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center' }}>
            <IconButton 
              size="large" 
              color="inherit"
              sx={{ 
                color: theme.palette.text.secondary,
                backgroundColor: theme.palette.grey[100],
                mr: 1,
                '&:hover': {
                  backgroundColor: theme.palette.grey[200],
                }
              }}
            >
              <SearchIcon />
            </IconButton>
            
            <IconButton
              size="large"
              aria-label="show new mails"
              color="inherit"
              sx={{ 
                color: theme.palette.text.secondary,
                backgroundColor: theme.palette.grey[100],
                mr: 1,
                '&:hover': {
                  backgroundColor: theme.palette.grey[200],
                }
              }}
            >
              <Badge badgeContent={4} color="error">
                <MailIcon />
              </Badge>
            </IconButton>
            
            <IconButton
              size="large"
              aria-label="show new notifications"
              color="inherit"
              sx={{ 
                color: theme.palette.text.secondary,
                backgroundColor: theme.palette.grey[100],
                mr: 2,
                '&:hover': {
                  backgroundColor: theme.palette.grey[200],
                }
              }}
            >
              <Badge badgeContent={17} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
            
            <Button 
              onClick={handleProfileMenuOpen}
              sx={{ 
                textTransform: 'none',
                borderRadius: 2,
                border: '1px solid',
                borderColor: 'divider',
                px: 2,
              }}
            >
              <Avatar 
                alt="User avatar"
                src="/images/avatars/avatar-0.png"
                sx={{ width: 32, height: 32 }}
              />
              <Box sx={{ ml: 1, textAlign: 'left' }}>
                <Typography variant="subtitle2" sx={{ color: 'text.primary', fontWeight: 600 }}>
                  John Doe
                </Typography>
                <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                  Administrator
                </Typography>
              </Box>
            </Button>
          </Box>
          
          <Box sx={{ display: { xs: 'flex', md: 'none' } }}>
            <IconButton
              size="large"
              aria-label="show more"
              aria-controls={mobileMenuId}
              aria-haspopup="true"
              onClick={handleMobileMenuOpen}
              color="inherit"
            >
              <MoreIcon />
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>
      {renderMobileMenu}
      {renderMenu}
    </Box>
  );
};

export default Header;
