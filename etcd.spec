%define debug_package %{nil}

Name:		etcd
Version:	0.1.1
Release:	1%{?dist}
Summary:	A highly-available key value store for shared configuration

License:	ASL 2.0
URL:		https://github.com/coreos/etcd/
Source0:	https://github.com/coreos/%{name}/archive/v%{version}/%{name}-v%{version}.tar.gz

BuildRequires:	golang

%description
A highly-available key value store for shared configuration.

%prep
%setup -q
sed -i "s/^\(VER=\).*HEAD)/\1%{version}/" ./scripts/release-version

%build
./build

%install
install -D -p  etcd %{buildroot}%{_bindir}/etcd
install -t %{buildroot}%{_bindir} etcd 


%files
%{_bindir}/etcd
%doc LICENSE README.md Documentation/internal-protocol-versioning.md

%changelog
* Mon Aug 26 2013 Luke Cypret <cypret@fedoraproject.org> - 0.1.1-1
Initial creation
