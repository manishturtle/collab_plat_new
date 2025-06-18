'use client';

import { useState } from 'react';
import { 
  ListItem, 
  ListItemButton, 
  ListItemIcon, 
  ListItemText, 
  Badge,
  Box,
  Typography
} from '@mui/material';
import Link from 'next/link';
import { ExpandLess, ExpandMore } from '@mui/icons-material';

interface SidebarItemProps {
  text: string;
  icon?: React.ReactNode;
  badge?: number | string;
  dot?: boolean;
  active?: boolean;
  expanded?: boolean;
  hasSubItems?: boolean;
  onClick?: () => void;
}

/**
 * SidebarItem component for rendering individual navigation items in the sidebar
 * 
 * @param props - The component props
 * @returns A sidebar navigation item component
 */
export const SidebarItem: React.FC<SidebarItemProps> = ({
  text,
  icon,
  badge,
  dot,
  active = false,
  expanded = false,
  hasSubItems = false,
  onClick
}) => {
  // Link is conditional - if it has subitems, no link is used
  const linkProps = hasSubItems 
    ? {} 
    : { component: Link, href: `/${text.toLowerCase().replace(/\s+/g, '-')}` };

  return (
    <ListItem disablePadding sx={{ display: 'block', mb: 0.5 }}>
      <ListItemButton
        onClick={onClick}
        sx={{
          px: 1.5,
          py: 0.75,
          borderRadius: 2,
          bgcolor: active ? 'primary.ultraLight' : 'transparent',
          color: active ? 'primary.main' : 'text.secondary',
          '&:hover': {
            bgcolor: active ? 'primary.ultraLight' : 'action.hover',
            color: active ? 'primary.main' : 'primary.main',
          },
        }}
        {...linkProps}
      >
        {icon && (
          <ListItemIcon 
            sx={{ 
              minWidth: 40, 
              color: 'inherit',
              fontSize: 20
            }}
          >
            {icon}
          </ListItemIcon>
        )}
        <ListItemText 
          primary={text} 
          primaryTypographyProps={{ 
            fontSize: '0.875rem',
            fontWeight: active ? 600 : 400
          }} 
        />
        {badge && (
          <Box
            component="span"
            sx={{
              bgcolor: 'primary.main',
              color: 'white',
              borderRadius: '9999px',
              px: 0.75,
              py: 0.125,
              fontSize: '0.75rem',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              minWidth: '1.25rem',
              height: '1.25rem',
            }}
          >
            {badge}
          </Box>
        )}
        {dot && (
          <Box
            component="span"
            sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              bgcolor: 'secondary.main',
            }}
          />
        )}
        {hasSubItems && (
          expanded ? <ExpandLess sx={{ color: 'text.secondary' }} /> : <ExpandMore sx={{ color: 'text.secondary' }} />
        )}
      </ListItemButton>
    </ListItem>
  );
};

export default SidebarItem;
