'use client';

import { Box, Typography, Avatar, Button, Grid } from '@mui/material';
import { useTranslation } from 'react-i18next';
import Image from 'next/image';

interface DetailSection {
  title: string;
  viewAllAction?: boolean;
  content: React.ReactNode;
}

interface FileItem {
  id: string;
  name: string;
  type: 'pdf' | 'doc' | 'file';
  size: string;
  date: string;
  icon: React.ReactNode;
  color: string;
}

interface LinkItem {
  id: string;
  title: string;
  thumbnail: string;
  source: string;
  date: string;
}

/**
 * ChatDetails component displays additional information about a chat conversation
 * including members, shared files, images, and links
 * 
 * @returns A sidebar component showing chat details and shared content
 */
const ChatDetails: React.FC = () => {
  const { t } = useTranslation();

  // Mock data for images
  const images = [
    '/images/shared/image-1.jpg',
    '/images/shared/image-2.jpg',
    '/images/shared/image-3.jpg',
    '/images/shared/image-4.jpg',
    '/images/shared/image-5.jpg',
    '/images/shared/image-6.jpg',
  ];

  // Mock data for files
  const files: FileItem[] = [
    {
      id: 'file1',
      name: '642 TB-DSHN_0001.pdf',
      type: 'pdf',
      size: '3.5MB',
      date: '12 Nov, 2023',
      icon: <span className="material-icons">picture_as_pdf</span>,
      color: '#FEE2E2' // light red
    },
    {
      id: 'file2',
      name: 'Report_week42.mp4',
      type: 'doc',
      size: '69.75MB',
      date: '12 Nov, 2023',
      icon: <span className="material-icons">description</span>,
      color: '#DBEAFE' // light blue
    },
    {
      id: 'file3',
      name: 'Marketing Campaign Brief.word',
      type: 'file',
      size: '2.2MB',
      date: '12 Nov, 2023',
      icon: <span className="material-icons">insert_drive_file</span>,
      color: '#DCFCE7' // light green
    }
  ];

  // Mock data for links
  const links: LinkItem[] = [
    {
      id: 'link1',
      title: 'Neuro Marketing: How brands are...',
      thumbnail: '/images/links/link-1.jpg',
      source: 'Youtube',
      date: '12 Nov, 2023'
    },
    {
      id: 'link2',
      title: 'Accomplish More Together',
      thumbnail: '/images/links/link-2.jpg',
      source: 'Confluence',
      date: '12 Nov, 2023'
    },
    {
      id: 'link3',
      title: 'How Apple and Nike have branded...',
      thumbnail: '/images/links/link-3.jpg',
      source: 'Youtube',
      date: '12 Nov, 2023'
    }
  ];

  // Sections to render
  const sections: DetailSection[] = [
    {
      title: 'Members',
      viewAllAction: true,
      content: (
        <>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            24 members
          </Typography>
        </>
      )
    },
    {
      title: 'Images',
      viewAllAction: true,
      content: (
        <Grid container spacing={1}>
          {images.map((image, index) => (
            <Grid key={`image-${index}`} sx={{ gridColumn: 'span 4 / span 4' }}>
              <Box
                sx={{
                  aspectRatio: '1/1',
                  borderRadius: 2,
                  overflow: 'hidden',
                  position: 'relative',
                  bgcolor: 'grey.100'
                }}
              >
                <Box
                  component="img"
                  src={image}
                  alt={`Shared image ${index + 1}`}
                  sx={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover'
                  }}
                />
              </Box>
            </Grid>
          ))}
        </Grid>
      )
    },
    {
      title: 'Files',
      viewAllAction: true,
      content: (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          {files.map((file) => (
            <Box
              key={file.id}
              sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}
            >
              <Box
                sx={{
                  width: 40,
                  height: 40,
                  borderRadius: 2,
                  bgcolor: file.color,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                {file.icon}
              </Box>
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: 500,
                    color: 'text.primary',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}
                >
                  {file.name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {file.size}
                </Typography>
              </Box>
              <Typography variant="caption" color="text.tertiary">
                {file.date}
              </Typography>
            </Box>
          ))}
        </Box>
      )
    },
    {
      title: 'Links',
      viewAllAction: true,
      content: (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          {links.map((link) => (
            <Box
              key={link.id}
              sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5 }}
            >
              <Box
                sx={{
                  width: 40,
                  height: 40,
                  borderRadius: 2,
                  overflow: 'hidden',
                  position: 'relative',
                  bgcolor: 'grey.100'
                }}
              >
                <Box
                  component="img"
                  src={link.thumbnail}
                  alt={link.title}
                  sx={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover'
                  }}
                />
              </Box>
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: 500,
                    color: 'text.primary',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}
                >
                  {link.title}
                </Typography>
                <Typography variant="caption" color="primary">
                  {link.source}
                </Typography>
              </Box>
              <Typography variant="caption" color="text.tertiary">
                {link.date}
              </Typography>
            </Box>
          ))}
        </Box>
      )
    }
  ];

  return (
    <Box
      sx={{
        width: '20rem',
        height: '100%',
        bgcolor: 'background.paper',
        borderLeft: 1,
        borderColor: 'divider',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      {/* Team Info Header */}
      <Box
        sx={{
          p: 3,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          borderBottom: 1,
          borderColor: 'divider'
        }}
      >
        <Avatar
          src="/images/groups/marketing-team.png"
          alt="Marketing Team"
          sx={{ width: 80, height: 80, mb: 1.5 }}
        />
        <Typography
          variant="h6"
          sx={{
            fontWeight: 600,
            color: 'text.primary',
            mb: 2
          }}
        >
          Marketing Team
        </Typography>

        <Box
          sx={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: 1,
            justifyContent: 'center'
          }}
        >
          <Button
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              p: 1,
              minWidth: '5rem',
              borderRadius: 1,
              color: 'text.secondary',
              '&:hover': {
                bgcolor: 'primary.ultraLight',
                color: 'primary.main'
              }
            }}
          >
            <span className="material-icons">notifications</span>
            <Typography variant="caption" sx={{ mt: 0.5 }}>
              {t('Notification')}
            </Typography>
          </Button>
          <Button
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              p: 1,
              minWidth: '5rem',
              borderRadius: 1,
              color: 'text.secondary',
              '&:hover': {
                bgcolor: 'primary.ultraLight',
                color: 'primary.main'
              }
            }}
          >
            <span className="material-icons">push_pin</span>
            <Typography variant="caption" sx={{ mt: 0.5 }}>
              {t('Pin Group')}
            </Typography>
          </Button>
          <Button
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              p: 1,
              minWidth: '5rem',
              borderRadius: 1,
              color: 'text.secondary',
              '&:hover': {
                bgcolor: 'primary.ultraLight',
                color: 'primary.main'
              }
            }}
          >
            <span className="material-icons">group</span>
            <Typography variant="caption" sx={{ mt: 0.5 }}>
              {t('Member')}
            </Typography>
          </Button>
          <Button
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              p: 1,
              minWidth: '5rem',
              borderRadius: 1,
              color: 'text.secondary',
              '&:hover': {
                bgcolor: 'primary.ultraLight',
                color: 'primary.main'
              }
            }}
          >
            <span className="material-icons">settings</span>
            <Typography variant="caption" sx={{ mt: 0.5 }}>
              {t('Setting')}
            </Typography>
          </Button>
        </Box>
      </Box>

      {/* Sections */}
      <Box
        sx={{
          flexGrow: 1,
          overflowY: 'auto',
          p: 3,
          display: 'flex',
          flexDirection: 'column',
          gap: 3,
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
        {sections.map((section, index) => (
          <Box key={`section-${index}`}>
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                mb: 1.5
              }}
            >
              <Typography
                variant="subtitle2"
                sx={{
                  fontWeight: 600,
                  color: 'text.primary',
                  fontSize: '0.875rem'
                }}
              >
                {section.title}
              </Typography>
              {section.viewAllAction && (
                <Typography
                  variant="caption"
                  component="a"
                  href="#"
                  sx={{
                    color: 'primary.main',
                    fontWeight: 500,
                    textDecoration: 'none',
                    '&:hover': {
                      textDecoration: 'underline'
                    }
                  }}
                >
                  {t('View All')}
                </Typography>
              )}
            </Box>
            {section.content}
          </Box>
        ))}
      </Box>
    </Box>
  );
};

export default ChatDetails;
