'use client';

import { useState } from 'react';
import { Box, Typography, List } from '@mui/material';
import SidebarItem from './sidebar-item';
import SidebarSubItem from './sidebar-sub-item';
import SidebarHeader from './sidebar-header';
import SidebarFooter from './sidebar-footer';
import { 
  Dashboard, 
  Layers, 
  Apps, 
  Assessment,
  Inventory2, 
  ReceiptLong, 
  Wysiwyg, 
  CollectionsBookmark,
  DeviceHub, 
  CreditCard, 
  RequestQuote, 
  Subscriptions,
  Payment
} from '@mui/icons-material';

interface MenuItem {
  text: string;
  icon?: React.ReactNode;
  badge?: number | string;
  dot?: boolean;
  active?: boolean;
  subItems?: string[];
  isHeader?: boolean;
}

/**
 * Configuration for sidebar menu items including headers, icons,
 * badges, and nested submenus
 */
export const sidebarMenuItems: MenuItem[] = [
  { text: 'Dashboard', icon: <Dashboard fontSize="small" /> },
  { text: 'Layouts', icon: <Layers fontSize="small" /> },
  { text: 'Apps', icon: <Apps fontSize="small" /> },
  { text: 'Reports', icon: <Assessment fontSize="small" />, badge: '2' },
  { 
    text: 'Products', 
    icon: <Inventory2 fontSize="small" />, 
    active: true,
    subItems: ['Category', 'Product', 'List', 'Package', 'Barcode', 'Option']
  },
  { text: 'Orders', icon: <ReceiptLong fontSize="small" />, dot: true },
  { text: 'My Tasks', icon: <Wysiwyg fontSize="small" /> },
  { text: 'Workflow', isHeader: true },
  { text: 'Gallery', icon: <CollectionsBookmark fontSize="small" /> },
  { text: 'Workflows', icon: <DeviceHub fontSize="small" /> },
  { text: 'My Tasks', icon: <CreditCard fontSize="small" />, dot: true },
  { text: 'Finance', isHeader: true },
  { text: 'Transactions', icon: <RequestQuote fontSize="small" /> },
  { text: 'Subscribers', icon: <Subscriptions fontSize="small" /> },
  { text: 'Payouts', icon: <Payment fontSize="small" /> },
];

/**
 * Sidebar component that displays the navigation menu with sections, items and subitems
 * 
 * @returns The main sidebar navigation component
 */
const Sidebar: React.FC = () => {
  const [expandedItems, setExpandedItems] = useState<string[]>(['Products']);

  const handleToggleExpand = (text: string): void => {
    setExpandedItems(prev => 
      prev.includes(text) 
        ? prev.filter(item => item !== text) 
        : [...prev, text]
    );
  };

  return (
    <Box 
      sx={{ 
        width: '16rem',
        height: '100%',
        display: 'flex', 
        flexDirection: 'column', 
        bgcolor: 'background.paper', 
        borderRight: 1, 
        borderColor: 'divider'
      }}
    >
      <SidebarHeader />
      
      <Box 
        component="nav" 
        sx={{ 
          flexGrow: 1, 
          p: 1, 
          overflowY: 'auto', 
          overflowX: 'hidden',
          '&::-webkit-scrollbar': {
            width: '6px',
          },
          '&::-webkit-scrollbar-track': {
            backgroundColor: '#f1f5f9',
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: '#cbd5e1',
            borderRadius: '6px',
          },
          '&::-webkit-scrollbar-thumb:hover': {
            backgroundColor: '#94a3b8',
          },
        }}
      >
        <List sx={{ py: 0 }}>
          {sidebarMenuItems.map((item, index) => {
            if (item.isHeader) {
              return (
                <Typography 
                  key={`header-${index}`}
                  variant="caption" 
                  sx={{ 
                    display: 'block', 
                    px: 2, 
                    py: 1, 
                    mt: 1,
                    color: 'text.secondary', 
                    textTransform: 'uppercase', 
                    fontWeight: 500,
                    fontSize: '0.75rem',
                  }}
                >
                  {item.text}
                </Typography>
              );
            }
            
            const isExpanded = item.subItems && expandedItems.includes(item.text);
            
            return (
              <Box key={`item-${index}`}>
                <SidebarItem
                  text={item.text}
                  icon={item.icon}
                  badge={item.badge}
                  dot={item.dot}
                  active={item.active}
                  expanded={!!isExpanded}
                  hasSubItems={!!item.subItems}
                  onClick={() => item.subItems && handleToggleExpand(item.text)}
                />
                
                {isExpanded && item.subItems && (
                  <Box sx={{ pl: 3 }}>
                    {item.subItems.map((subItem, subIndex) => (
                      <SidebarSubItem 
                        key={`subitem-${subIndex}`} 
                        text={subItem}
                        active={subItem === 'Product'}
                      />
                    ))}
                  </Box>
                )}
              </Box>
            );
          })}
        </List>
      </Box>
      
      <SidebarFooter />
    </Box>
  );
};

export default Sidebar;
