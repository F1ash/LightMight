Name: LightMight
Version: 0.1.0
Release: %(date +%Y%m%d_%H%M)%{?dist}
Summary: Programm for file`s resource publication and transmittion in local network
Summary(ru): Программа для публикации и обмена ресурсами в локальной сети
Group: Applications/Network
License: GPL
Source0: %{name}-%{version}.tar.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
URL: https://github.com/F1ash/LightMight
BuildArch: noarch

%if %{defined fedora}
Requires: python >= 2.6, dbus-python, PyQt4 >= 4.7, avahi, avahi-ui-tools 
BuildRequires: desktop-file-utils
%endif

%description
LightMight
Programm for resource publication and transmittion in local network

%description -l ru
LightMight
Программа для публикации и обмена ресурсами в локальной сети

%prep
%setup -q

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/%{name}
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/applications
install -D -m 755 -p %{name} $RPM_BUILD_ROOT/%{_bindir}/%{name}
install -D -m 644 -p contents/icons/%{name}.png $RPM_BUILD_ROOT/%{_datadir}/icons/hicolor/128x128/apps/%{name}.png
install -D -m 644 -p contents/icons/%{name}.png  $RPM_BUILD_ROOT/%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
install -D -m 644 -p contents/icons/%{name}.png  $RPM_BUILD_ROOT/%{_datadir}/icons/hicolor/24x24/apps/%{name}.png
install -D -m 644 -p contents/icons/%{name}.png  $RPM_BUILD_ROOT/%{_datadir}/icons/hicolor/256x256/apps/%{name}.png
install -D -m 644 -p contents/icons/%{name}.png  $RPM_BUILD_ROOT/%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
install -D -m 644 -p contents/icons/%{name}.png  $RPM_BUILD_ROOT/%{_datadir}/icons/hicolor/64x64/apps/%{name}.png
install -D -m 644 -p contents/icons/%{name}.png $RPM_BUILD_ROOT/%{_datadir}/pixmaps/%{name}.png
#cp -r contents/code $RPM_BUILD_ROOT/%{_datadir}/%{name}/
#cp -r contents/icons $RPM_BUILD_ROOT/%{_datadir}/%{name}/
cp -r * $RPM_BUILD_ROOT/%{_datadir}/%{name}/

%if %{defined fedora}
desktop-file-install --delete-original		\
	--dir ${RPM_BUILD_ROOT}%{_datadir}/applications lightMight.desktop
desktop-file-validate %{buildroot}/%{_datadir}/applications/lightMight.desktop
%endif


%files
%defattr(-,root,root)
%{_bindir}/%{name}
%{_datadir}/icons/hicolor/128x128/apps/%{name}.png
%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
%{_datadir}/icons/hicolor/24x24/apps/%{name}.png
%{_datadir}/icons/hicolor/256x256/apps/%{name}.png
%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
%{_datadir}/icons/hicolor/64x64/apps/%{name}.png
%{_datadir}/pixmaps/%{name}.png
%{_datadir}/applications/lightMight.desktop
%{_datadir}/%{name}/contents/icons/*
%{_datadir}/%{name}/contents/code/*
%{_datadir}/%{name}/*
%dir %{_datadir}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
touch --no-create %{_datadir}/icons/hicolor || :
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
	%{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi

%postun
touch --no-create %{_datadir}/icons/hicolor || :
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
	%{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi

%changelog

* Thu Jun 9 2011 Fl@sh <no@mail.me>	-	0.1.0
-- Build began ;)
