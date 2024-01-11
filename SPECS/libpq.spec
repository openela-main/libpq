%global majorversion 13
%global obsoletes_version %( echo $(( %majorversion + 1 )) )

Summary: PostgreSQL client library
Name: libpq
Version: %{majorversion}.11
Release: 1%{?dist}

License: PostgreSQL
Url: http://www.postgresql.org/

Source0: https://ftp.postgresql.org/pub/source/v%{version}/postgresql-%{version}.tar.bz2
Source1: https://ftp.postgresql.org/pub/source/v%{version}/postgresql-%{version}.tar.bz2.sha256


# Comments for these patches are in the patch files.
Patch1: libpq-10.3-rpm-pgsql.patch
Patch2: libpq-10.3-var-run-socket.patch
Patch3: libpq-13.1-symbol-versioning.patch

BuildRequires: gcc
BuildRequires: glibc-devel bison flex gawk
BuildRequires: zlib-devel
BuildRequires: openssl-devel
BuildRequires: krb5-devel
BuildRequires: openldap-devel
BuildRequires: gettext
BuildRequires: multilib-rpm-config

Obsoletes: postgresql-libs < %obsoletes_version
Provides: postgresql-libs = %version-%release


%description
The libpq package provides the essential shared library for any PostgreSQL
client program or interface.  You will need to install this package to use any
other PostgreSQL package or any clients that need to connect to a PostgreSQL
server.


%package devel
Summary: Development files for building PostgreSQL client tools
Requires: %name%{?_isa} = %version-%release
# Historically we had 'postgresql-devel' package which was used for building
# both PG clients and PG server modules;  let's have this fake provide to cover
# most of the depending packages and the rest (those which want to build server
# modules) need to be fixed to require postgresql-server-devel package.
Provides: postgresql-devel = %version-%release
Obsoletes: postgresql-devel < %obsoletes_version

%description devel
The libpq package provides the essential shared library for any PostgreSQL
client program or interface.  You will need to install this package to build any
package or any clients that need to connect to a PostgreSQL server.


%prep
( cd "$(dirname "%SOURCE1")" ; sha256sum -c "%SOURCE1" )
%autosetup -n postgresql-%{version} -p1

# remove .gitignore files to ensure none get into the RPMs (bug #642210)
find . -type f -name .gitignore | xargs rm


%build
# complements symbol-versioning patch
export SYMBOL_VERSION_PREFIX=RHPG_

# We don't build server nor client (e.g. /bin/psql) binaries in this package, so
# we can disable some configure options.
%configure \
    --disable-rpath \
    --with-ldap \
    --with-openssl \
    --with-gssapi \
    --enable-nls \
    --without-readline \
    --datadir=%_datadir/pgsql

%global build_subdirs \\\
        src/include \\\
        src/common \\\
        src/port \\\
        src/interfaces/libpq \\\
        src/bin/pg_config

for subdir in %build_subdirs; do
    %make_build -C "$subdir"
done


%install
for subdir in %build_subdirs; do
    %make_install -C "$subdir"
done

# remove files not to be packaged
find $RPM_BUILD_ROOT -name '*.a' -delete
rm -r $RPM_BUILD_ROOT%_includedir/pgsql/server

%multilib_fix_c_header --file "%_includedir/pg_config.h"
%multilib_fix_c_header --file "%_includedir/pg_config_ext.h"

find_lang_bins ()
{
    lstfile=$1 ; shift
    cp /dev/null "$lstfile"
    for binary; do
        %find_lang "$binary"-%majorversion
        cat "$binary"-%majorversion.lang >>"$lstfile"
    done
}

find_lang_bins %name.lst        libpq5
find_lang_bins %name-devel.lst  pg_config


%files -f %name.lst
%license COPYRIGHT
%_libdir/libpq.so.*
%dir %_datadir/pgsql
%doc %_datadir/pgsql/pg_service.conf.sample


%files devel -f %name-devel.lst
%_bindir/pg_config
%_includedir/*
%_libdir/libpq.so
%_libdir/pkgconfig/libpq.pc


%changelog
* Wed Jun 21 2023 Masahiro Matsuya <mmatsuya@redhat.com> - 13.11-1
- Rebase to 13.11
  Resolves: #2171369

* Mon Nov 29 2021 Marek Kulik <mkulik@redhat.com> - 13.5-1
- Rebase to 13.5
  Resolves: #2023294

* Mon May 31 2021 Honza Horak <hhorak@redhat.com> - 13.3-1
- Rebase to 13.3
  Resolves: #1966146

* Tue Feb 16 2021 Honza Horak <hhorak@redhat.com> - 13.2-1
- Rebase to 13.2
  Related: #1855776

* Tue Nov 17 2020 Patrik Novotný <panovotn@redhat.com> - 13.1-1
- Rebase to upstream release 13.1
  Resolves: BZ#1855776
  (BZ#1856242 particuarly)

* Mon Aug 17 2020 Patrik Novotný <panovotn@redhat.com> - 12.4-1
- Rebase to upstream release 12.4

* Tue Jun 16 2020 Patrik Novotný <panovotn@redhat.com> - 12.3-1
- Rebase to upstream release 12.3

* Tue Nov 19 2019 Patrik Novotný <panovotn@redhat.com> - 12.1-3
- Rebuild with rebased symbol versioning patch

* Fri Nov 15 2019 Patrik Novotný <panovotn@redhat.com> - 12.1-2
- Rebuild with rebased symbol versioning patch

* Tue Nov 12 2019 Patrik Novotný <panovotn@redhat.com> - 12.1-1
- Rebase to upstream release 12.1

* Fri Nov 08 2019 Honza Horak <hhorak@redhat.com> - 12.0-2
- Bump release for a new build with gating.yaml added
  Related: #1749461

* Thu Oct 03 2019 Patrik Novotný <panovotn@redhat.com> - 12.0-1
- Initial release for upstream version 12.0

* Wed Aug 08 2018 Pavel Raiskup <praiskup@redhat.com> - 10.5-1
- update to 10.5 per release notes:
  https://www.postgresql.org/docs/10/static/release-10-5.html

* Fri Jul 13 2018 Pavel Raiskup <praiskup@redhat.com> - 10.4-2
- ABI/symbol versioning

* Thu Jul 12 2018 Pavel Raiskup <praiskup@redhat.com> - 10.4-1
- rebase to the latest upstream release

* Fri Apr 13 2018 Pavel Raiskup <praiskup@redhat.com> - 10.3-1
- initial release, packaging inspired by postgresql.spec
- provide postgresql-devel to avoid fixing all the client packages
