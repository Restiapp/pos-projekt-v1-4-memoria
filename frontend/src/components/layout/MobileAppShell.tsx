import { AppShell, Group, Burger, ActionIcon, useMantineTheme } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { IconToolsKitchen2, IconArmchair, IconClipboardList, IconSettings } from '@tabler/icons-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useState } from 'react';

interface MobileAppShellProps {
    children: React.ReactNode;
    title?: React.ReactNode;
}

export const MobileAppShell = ({ children, title }: MobileAppShellProps) => {
    const [opened, { toggle }] = useDisclosure();
    const theme = useMantineTheme();
    const navigate = useNavigate();
    const location = useLocation();

    // Active tab state
    const getActiveTab = () => {
        if (location.pathname.includes('/tables')) return 'tables';
        if (location.pathname.includes('/kds')) return 'kds';
        if (location.pathname.includes('/orders')) return 'orders';
        if (location.pathname.includes('/admin')) return 'admin';
        return 'tables';
    };
    const activeTab = getActiveTab();

    const navItems = [
        { id: 'tables', icon: IconArmchair, label: 'Asztalok', path: '/tables' },
        { id: 'kds', icon: IconToolsKitchen2, label: 'KDS', path: '/kds' },
        { id: 'orders', icon: IconClipboardList, label: 'Rendelések', path: '/orders' }, // Placeholder path
        { id: 'admin', icon: IconSettings, label: 'Admin', path: '/admin/tables' },
    ];

    return (
        <AppShell
            header={{ height: 60 }}
            footer={{ height: 70 }} // Increased height for bottom nav
            padding="md"
        >
            <AppShell.Header>
                <Group h="100%" px="md" justify="space-between">
                    <Group>
                        {/* Burger menu for potential sidebar later */}
                        {/* <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" /> */}
                        <div style={{ fontWeight: 700, fontSize: '1.2rem' }}>RESTI POS</div>
                    </Group>
                    {title && <div>{title}</div>}
                </Group>
            </AppShell.Header>

            <AppShell.Main>
                {children}
            </AppShell.Main>

            <AppShell.Footer p={0} style={{ zIndex: 200 }}>
                <Group justify="space-around" h="100%" align="center" gap={0}>
                    {navItems.map((item) => {
                        const isActive = activeTab === item.id;
                        return (
                            <ActionIcon
                                key={item.id}
                                variant={isActive ? 'filled' : 'subtle'}
                                color={isActive ? 'blue' : 'gray'}
                                size="xl"
                                radius="md"
                                style={{ width: '25%', height: '100%', borderRadius: 0 }}
                                onClick={() => navigate(item.path)}
                            >
                                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                                    <item.icon size={24} stroke={1.5} />
                                    <span style={{ fontSize: '0.7rem', fontWeight: 500 }}>{item.label}</span>
                                </div>
                            </ActionIcon>
                        );
                    })}
                </Group>
            </AppShell.Footer>
        </AppShell>
    );
};
