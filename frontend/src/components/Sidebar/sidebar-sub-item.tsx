'use client';

import { ListItem, ListItemButton, ListItemText } from '@mui/material';
import Link from 'next/link';

interface SidebarSubItemProps {
  text: string;
  active?: boolean;
}

/**
 * SidebarSubItem component for rendering sub-items in the sidebar navigation
 * 
 * @param props - Component props
 * @returns A sub-item component for sidebar navigation
 */
const SidebarSubItem: React.FC<SidebarSubItemProps> = ({
  text,
  active = false
}) => {
  return (
    <ListItem disablePadding sx={{ display: 'block' }}>
      <ListItemButton
        component={Link}
        href={`/products/${text.toLowerCase().replace(/\s+/g, '-')}`}
        sx={{
          px: 2,
          py: 1,
          color: active ? 'primary.main' : 'text.secondary',
          fontWeight: active ? 600 : 400,
          fontSize: '0.875rem',
          borderRadius: 1,
          '&:hover': {
            bgcolor: 'action.hover',
            color: 'primary.main',
          },
        }}
      >
        <ListItemText 
          primary={text} 
          primaryTypographyProps={{ 
            fontSize: '0.875rem',
            fontWeight: active ? 600 : 400
          }}
        />
      </ListItemButton>
    </ListItem>
  );
};

export default SidebarSubItem;
