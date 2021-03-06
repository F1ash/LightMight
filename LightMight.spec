Name: LightMight
Version: 0.21.39
Release: 1%{?dist}
Summary: Programm for resource publication and transmission in local network
Summary(ru): Программа для публикации и обмена ресурсами в локальной сети
Group: Applications/Network
License: GPLv2+
Source0: %{name}-%{version}.tar.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
URL: https://github.com/F1ash/LightMight
BuildArch: noarch

%if %{defined fedora}
Requires: python, dbus-python, PyQt4, avahi, avahi-ui-tools, m2crypto
BuildRequires: desktop-file-utils
%endif

%description
LightMight
Programm for resource publication and transmission in local network

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
#%{_datadir}/%{name}/contents/icons/*
#%{_datadir}/%{name}/contents/code/*
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

* Fri Mar 02 2012 Fl@sh <kaperang07@gmail.com> - 0.21.39-1
- deleted added avahi-compat-libdns_sd require;
- version updated

* Sun Feb 26 2012 Fl@sh <kaperang07@gmail.com> - 0.19.37-1.R
- added m2crypto & deleted openssl requires;
- version updated

* Mon Dec 5 2011 Fl@sh <kaperang07@gmail.com> - 0.18.35-1.R
- version updated

* Sun Oct 30 2011 Fl@sh <kaperang07@gmail.com> - 0.10.22-1
- version updated

* Sat Oct 29 2011 Fl@sh <kaperang07@gmail.com> - 0.10.21-1
- version updated

* Thu Oct 20 2011 Fl@sh <kaperang07@gmail.com> - 0.9.20-1
- version updated

* Tue Oct 18 2011 Fl@sh <kaperang07@gmail.com> - 0.9.19-1
- version updated

* Fri Jun 24 2011 Fl@sh <kaperang07@gmail.com> - 0.5.10-1
- added avahi-compat-libdns_sd dependence
	and python >= 3.0 conflict

* Sun Jun 19 2011 Fl@sh <kaperang07@gmail.com> - 0.3.9-1
- added openssl dependence

* Thu Jun 9 2011 Fl@sh <kaperang07@gmail.com> - 0.1.0-1
- Initial build
